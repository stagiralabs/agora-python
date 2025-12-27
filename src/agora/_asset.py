from fractions import Fraction
from typing import Dict, List, Optional, Set, Tuple, Union, cast
from abc import ABC, abstractmethod
import json


TargetSuccess = Dict[str, Optional[Tuple[Fraction, Optional[str]]]]


class Asset(ABC):
    """
    Abstract base class for all asset types.
    """

    @abstractmethod
    def referenced_target_ids(self) -> Set[str]:
        """Get the set of all targets referenced by this asset."""
        pass

    @abstractmethod
    def simplify(
        self, target_success: TargetSuccess, watermark_time: Fraction
    ) -> "Asset":
        """
        Simplify the asset based on target success information and watermark time.

        Note: referenced_target_ids() must be a subset of target_success.keys()
        The set of referenced_target_ids of a simplified asset must be
        a subset of the referenced_target_ids of the original. Furthermore,
        if a target is solved, the simplified asset cannot reference this target.
        When we eventually have no referenced targets left, we must
        be a ConstantAsset. This must be guaranteed to happen in finite time.
        """
        pass

    @abstractmethod
    def lower_bound(self, watermark_time: Fraction) -> Fraction:
        """Should provide a lower bound on the ConstantAsset resulting from repeated simplification."""
        pass

    @abstractmethod
    def upper_bound(self, watermark_time: Fraction) -> Fraction:
        """Should provide an upper bound on the ConstantAsset resulting from repeated simplification."""
        pass


class ConstantAsset(Asset):
    """An asset with a constant value."""

    def __init__(self, constant: Fraction):
        self.constant = constant

    def referenced_target_ids(self) -> Set[str]:
        return set()

    def simplify(
        self, target_success: TargetSuccess, watermark_time: Fraction
    ) -> "ConstantAsset":
        assert self.referenced_target_ids().issubset(target_success.keys())
        return self

    def lower_bound(self, watermark_time: Fraction) -> Fraction:
        return self.constant

    def upper_bound(self, watermark_time: Fraction) -> Fraction:
        return self.constant


class SatisfiedByAsset(Asset):
    """
    1 if the target is proven on time, 0 otherwise.
    """

    def __init__(self, target: str, stop_time: Fraction):
        self.target = target
        self.stop_time = stop_time

    def referenced_target_ids(self) -> Set[str]:
        return {self.target}

    def simplify(
        self, target_success: TargetSuccess, watermark_time: Fraction
    ) -> Asset:
        assert self.referenced_target_ids().issubset(target_success.keys())

        target_result = target_success[self.target]

        if target_result is not None:
            proven_time, author = target_result
            if proven_time <= self.stop_time:
                return ConstantAsset(Fraction(1))
            return ConstantAsset(Fraction(0))

        if watermark_time > self.stop_time:
            return ConstantAsset(Fraction(0))

        return self

    def lower_bound(self, watermark_time: Fraction) -> Fraction:
        return Fraction(0)

    def upper_bound(self, watermark_time: Fraction) -> Fraction:
        return Fraction(1)


class AgentsSatisfyByAsset(Asset):
    """
    1 if the target is proven on time by one of the listed agents, 0 otherwise.
    """

    def __init__(self, target: str, agent_ids: List[str], stop_time: Fraction):
        self.target = target
        self.agent_ids = agent_ids
        self.stop_time = stop_time

    def referenced_target_ids(self) -> Set[str]:
        return {self.target}

    def simplify(
        self, target_success: TargetSuccess, watermark_time: Fraction
    ) -> Asset:
        assert self.referenced_target_ids().issubset(target_success.keys())

        target_result = target_success[self.target]

        if target_result is not None:
            proven_time, author = target_result
            if proven_time <= self.stop_time and author in self.agent_ids:
                return ConstantAsset(Fraction(1))
            else:
                return ConstantAsset(Fraction(0))

        if watermark_time > self.stop_time:
            return ConstantAsset(Fraction(0))

        return self

    def lower_bound(self, watermark_time: Fraction) -> Fraction:
        return Fraction(0)

    def upper_bound(self, watermark_time: Fraction) -> Fraction:
        return Fraction(1)


class TimeRemainingAsset(Asset):
    """
    The amount of time target is satisfied before stop_time
    (or 0 if not satisfied by then).
    """

    def __init__(self, target: str, stop_time: Fraction):
        self.target = target
        self.stop_time = stop_time

    def referenced_target_ids(self) -> Set[str]:
        return {self.target}

    def simplify(
        self, target_success: TargetSuccess, watermark_time: Fraction
    ) -> Asset:
        assert self.referenced_target_ids().issubset(target_success.keys())

        target_result = target_success[self.target]

        if target_result is not None:
            proven_time, author = target_result
            if proven_time <= self.stop_time:
                return ConstantAsset(self.stop_time - proven_time)
            return ConstantAsset(Fraction(0))

        if watermark_time > self.stop_time:
            return ConstantAsset(Fraction(0))

        return self

    def lower_bound(self, watermark_time: Fraction) -> Fraction:
        return Fraction(0)

    def upper_bound(self, watermark_time: Fraction) -> Fraction:
        return max(self.stop_time - watermark_time, Fraction(0))


class MaxAsset(Asset):
    """Returns the maximum value among a list of assets."""

    def __init__(self, assets: List[Asset]):
        assert len(assets) > 0, "MaxAsset must have non-empty assets list"
        self.assets = assets

    def referenced_target_ids(self) -> Set[str]:
        return set().union(*[asset.referenced_target_ids() for asset in self.assets])

    def simplify(
        self, target_success: TargetSuccess, watermark_time: Fraction
    ) -> Asset:
        assert self.referenced_target_ids().issubset(target_success.keys())

        simplified_assets = [
            asset.simplify(target_success, watermark_time) for asset in self.assets
        ]

        if all(isinstance(asset, ConstantAsset) for asset in simplified_assets):
            constants = [
                cast(ConstantAsset, asset).constant for asset in simplified_assets
            ]
            return ConstantAsset(max(constants))

        return MaxAsset(simplified_assets)

    def lower_bound(self, watermark_time: Fraction) -> Fraction:
        return max([asset.lower_bound(watermark_time) for asset in self.assets])

    def upper_bound(self, watermark_time: Fraction) -> Fraction:
        return max([asset.upper_bound(watermark_time) for asset in self.assets])


class MinAsset(Asset):
    """Returns the minimum value among a list of assets."""

    def __init__(self, assets: List[Asset]):
        assert len(assets) > 0, "MinAsset must have non-empty assets list"
        self.assets = assets

    def referenced_target_ids(self) -> Set[str]:
        return set().union(*[asset.referenced_target_ids() for asset in self.assets])

    def simplify(
        self, target_success: TargetSuccess, watermark_time: Fraction
    ) -> Asset:
        assert self.referenced_target_ids().issubset(target_success.keys())

        simplified_assets = [
            asset.simplify(target_success, watermark_time) for asset in self.assets
        ]

        if all(isinstance(asset, ConstantAsset) for asset in simplified_assets):
            constants = [
                cast(ConstantAsset, asset).constant for asset in simplified_assets
            ]
            return ConstantAsset(min(constants))

        return MinAsset(simplified_assets)

    def lower_bound(self, watermark_time: Fraction) -> Fraction:
        return min([asset.lower_bound(watermark_time) for asset in self.assets])

    def upper_bound(self, watermark_time: Fraction) -> Fraction:
        return min([asset.upper_bound(watermark_time) for asset in self.assets])


class LinearCombinationAsset(Asset):
    """Represents a linear combination of assets with coefficients."""

    def __init__(self, terms: List[Tuple[Fraction, Asset]]):
        self.terms = terms

    def referenced_target_ids(self) -> Set[str]:
        return set().union(*[gen.referenced_target_ids() for coeff, gen in self.terms])

    def simplify(
        self, target_success: TargetSuccess, watermark_time: Fraction
    ) -> Asset:
        assert self.referenced_target_ids().issubset(target_success.keys())

        simplified_terms = [
            (coefficient, generator.simplify(target_success, watermark_time))
            for coefficient, generator in self.terms
        ]

        if all(
            isinstance(generator, ConstantAsset)
            for coefficient, generator in simplified_terms
        ):
            constants = [
                coefficient * cast(ConstantAsset, generator).constant
                for coefficient, generator in simplified_terms
            ]
            return ConstantAsset(sum(constants, Fraction(0)))

        return LinearCombinationAsset(simplified_terms)

    def lower_bound(self, watermark_time: Fraction) -> Fraction:
        return sum(
            [
                coeff
                * (
                    gen.lower_bound(watermark_time)
                    if coeff >= 0
                    else gen.upper_bound(watermark_time)
                )
                for coeff, gen in self.terms
            ],
            Fraction(0),
        )

    def upper_bound(self, watermark_time: Fraction) -> Fraction:
        return sum(
            [
                coeff
                * (
                    gen.upper_bound(watermark_time)
                    if coeff >= 0
                    else gen.lower_bound(watermark_time)
                )
                for coeff, gen in self.terms
            ],
            Fraction(0),
        )


class PriceySatisfiedByAsset(Asset):
    """
    1-price if the target is proven on time, -price otherwise.
    """

    def __init__(
        self,
        target: str,
        stop_time: Fraction,
        price: Fraction,
    ):
        self.target = target
        self.stop_time = stop_time
        self.price = price

    def referenced_target_ids(self) -> Set[str]:
        return {self.target}

    def simplify(
        self, target_success: TargetSuccess, watermark_time: Fraction
    ) -> Asset:
        assert self.referenced_target_ids().issubset(target_success.keys())

        target_result = target_success[self.target]

        if target_result is not None:
            proven_time, author = target_result
            if proven_time <= self.stop_time:
                return ConstantAsset(Fraction(1) - self.price)
            return ConstantAsset(-self.price)

        if watermark_time > self.stop_time:
            return ConstantAsset(-self.price)

        return self

    def lower_bound(self, watermark_time: Fraction) -> Fraction:
        return -self.price

    def upper_bound(self, watermark_time: Fraction) -> Fraction:
        return Fraction(1) - self.price


class PriceyTimeRemainingAsset(Asset):
    """
    An asset which is worth -max_loss if the target is proven after stop_time
    and whose value changes linearly at earlier times such that it's worth
    0 at break_even_time.
    Mathematically, the final value is:
    max_loss*[max(stop_time-proven_time,0)/(stop_time-break_even_time) - 1]
    """

    def __init__(
        self,
        target: str,
        break_even_time: Fraction,
        stop_time: Fraction,
        max_loss: Fraction,
    ):
        assert stop_time > break_even_time, "stop_time must be > break_even_time"
        assert max_loss > 0, "max_loss must be > 0"

        self.target = target
        self.break_even_time = break_even_time
        self.stop_time = stop_time
        self.max_loss = max_loss

    def referenced_target_ids(self) -> Set[str]:
        return {self.target}

    def simplify(
        self, target_success: TargetSuccess, watermark_time: Fraction
    ) -> Asset:
        assert self.referenced_target_ids().issubset(target_success.keys())

        target_result = target_success[self.target]

        if target_result is not None:
            proven_time, author = target_result
            if proven_time <= self.stop_time:
                time_remaining = max(self.stop_time - proven_time, Fraction(0))
                value = self.max_loss * (
                    time_remaining / (self.stop_time - self.break_even_time)
                    - Fraction(1)
                )
                return ConstantAsset(value)
            return ConstantAsset(-self.max_loss)

        if watermark_time > self.stop_time:
            return ConstantAsset(-self.max_loss)

        return self

    def lower_bound(self, watermark_time: Fraction) -> Fraction:
        return -self.max_loss

    def upper_bound(self, watermark_time: Fraction) -> Fraction:
        time_remaining = max(self.stop_time - watermark_time, Fraction(0))
        return self.max_loss * (
            time_remaining / (self.stop_time - self.break_even_time) - Fraction(1)
        )


def asset_to_str(asset: Asset) -> str:
    """Convert an asset to its string representation."""

    def fraction_to_str(f: Fraction) -> str:
        if f.denominator == 1:
            return str(f.numerator)
        return f"{f.numerator}/{f.denominator}"

    if isinstance(asset, ConstantAsset):
        return f"ConstantAsset({fraction_to_str(asset.constant)})"

    elif isinstance(asset, SatisfiedByAsset):
        return f"SatisfiedByAsset({json.dumps(asset.target)},{fraction_to_str(asset.stop_time)})"

    elif isinstance(asset, AgentsSatisfyByAsset):
        agent_ids_str = json.dumps(asset.agent_ids)
        return f"AgentsSatisfyByAsset({json.dumps(asset.target)},{agent_ids_str},{fraction_to_str(asset.stop_time)})"

    elif isinstance(asset, TimeRemainingAsset):
        return f"TimeRemainingAsset({json.dumps(asset.target)},{fraction_to_str(asset.stop_time)})"

    elif isinstance(asset, MaxAsset):
        assets_str = ",".join([asset_to_str(a) for a in asset.assets])
        return f"MaxAsset([{assets_str}])"

    elif isinstance(asset, MinAsset):
        assets_str = ",".join([asset_to_str(a) for a in asset.assets])
        return f"MinAsset([{assets_str}])"

    elif isinstance(asset, LinearCombinationAsset):
        terms_str = ",".join(
            [
                f"({fraction_to_str(coeff)},{asset_to_str(gen)})"
                for coeff, gen in asset.terms
            ]
        )
        return f"LinearCombinationAsset([{terms_str}])"

    elif isinstance(asset, PriceySatisfiedByAsset):
        return (
            f"PriceySatisfiedByAsset({json.dumps(asset.target)},"
            f"{fraction_to_str(asset.stop_time)},"
            f"{fraction_to_str(asset.price)})"
        )

    elif isinstance(asset, PriceyTimeRemainingAsset):
        return (
            f"PriceyTimeRemainingAsset({json.dumps(asset.target)},"
            f"{fraction_to_str(asset.break_even_time)},"
            f"{fraction_to_str(asset.stop_time)},"
            f"{fraction_to_str(asset.max_loss)})"
        )

    else:
        raise ValueError(f"Unknown asset type: {type(asset)}")


def str_to_asset(string: str) -> Asset:
    """
    Convert a string representation back to an asset.

    For any starting asset, str_to_asset(asset_to_str(asset)) should have the same data.
    For any string such that str_to_asset(string) returns an asset (and not an error),
    we should have asset_to_str(str_to_asset(string)) == string.
    """

    def parse_fraction(s: str) -> Fraction:
        if "/" in s:
            parts = s.split("/")
            return Fraction(int(parts[0]), int(parts[1]))
        return Fraction(int(s))

    def find_matching_paren(s: str, start: int) -> int:
        """Find the matching closing parenthesis."""
        count = 0
        for i in range(start, len(s)):
            if s[i] == "(":
                count += 1
            elif s[i] == ")":
                count -= 1
                if count == 0:
                    return i
        raise ValueError("Unmatched parenthesis")

    def find_matching_bracket(s: str, start: int) -> int:
        """Find the matching closing bracket."""
        count = 0
        for i in range(start, len(s)):
            if s[i] == "[":
                count += 1
            elif s[i] == "]":
                count -= 1
                if count == 0:
                    return i
        raise ValueError("Unmatched bracket")

    def parse_arguments(args_str: str) -> List[str]:
        """Parse comma-separated arguments, respecting nested structures."""
        args = []
        current = []
        depth = 0
        bracket_depth = 0
        in_string = False
        escape = False

        for char in args_str:
            if escape:
                current.append(char)
                escape = False
                continue

            if char == "\\" and in_string:
                escape = True
                current.append(char)
                continue

            if char == '"' and not escape:
                in_string = not in_string
                current.append(char)
                continue

            if not in_string:
                if char == "(":
                    depth += 1
                elif char == ")":
                    depth -= 1
                elif char == "[":
                    bracket_depth += 1
                elif char == "]":
                    bracket_depth -= 1
                elif char == "," and depth == 0 and bracket_depth == 0:
                    args.append("".join(current))
                    current = []
                    continue

            current.append(char)

        if current:
            args.append("".join(current))

        return args

    string = string.strip()

    if string.startswith("ConstantAsset("):
        end = find_matching_paren(string, string.index("("))
        arg = string[14:end]
        return ConstantAsset(parse_fraction(arg))

    elif string.startswith("SatisfiedByAsset("):
        end = find_matching_paren(string, string.index("("))
        args = parse_arguments(string[17:end])
        target = json.loads(args[0])
        stop_time = parse_fraction(args[1])
        return SatisfiedByAsset(target, stop_time)

    elif string.startswith("AgentsSatisfyByAsset("):
        end = find_matching_paren(string, string.index("("))
        args = parse_arguments(string[21:end])
        target = json.loads(args[0])
        agent_ids = json.loads(args[1])
        stop_time = parse_fraction(args[2])
        return AgentsSatisfyByAsset(target, agent_ids, stop_time)

    elif string.startswith("TimeRemainingAsset("):
        end = find_matching_paren(string, string.index("("))
        args = parse_arguments(string[19:end])
        target = json.loads(args[0])
        stop_time = parse_fraction(args[1])
        return TimeRemainingAsset(target, stop_time)

    elif string.startswith("MaxAsset("):
        end = find_matching_paren(string, string.index("("))
        list_content = string[9:end]
        list_content = list_content.strip()
        if not (list_content.startswith("[") and list_content.endswith("]")):
            raise ValueError("MaxAsset expects a list")
        list_content = list_content[1:-1]
        if not list_content:
            raise ValueError("MaxAsset must have non-empty assets list")
        asset_strs = parse_arguments(list_content)
        assets = [str_to_asset(s) for s in asset_strs]
        return MaxAsset(assets)

    elif string.startswith("MinAsset("):
        end = find_matching_paren(string, string.index("("))
        list_content = string[9:end]
        list_content = list_content.strip()
        if not (list_content.startswith("[") and list_content.endswith("]")):
            raise ValueError("MinAsset expects a list")
        list_content = list_content[1:-1]
        if not list_content:
            raise ValueError("MinAsset must have non-empty assets list")
        asset_strs = parse_arguments(list_content)
        assets = [str_to_asset(s) for s in asset_strs]
        return MinAsset(assets)

    elif string.startswith("LinearCombinationAsset("):
        end = find_matching_paren(string, string.index("("))
        list_content = string[23:end]
        list_content = list_content.strip()
        if not (list_content.startswith("[") and list_content.endswith("]")):
            raise ValueError("LinearCombinationAsset expects a list")
        list_content = list_content[1:-1]
        term_strs = parse_arguments(list_content)

        terms = []
        for term_str in term_strs:
            term_str = term_str.strip()
            if not (term_str.startswith("(") and term_str.endswith(")")):
                raise ValueError("Each term must be a tuple")
            term_str = term_str[1:-1]
            parts = parse_arguments(term_str)
            coeff = parse_fraction(parts[0])
            asset = str_to_asset(parts[1])
            terms.append((coeff, asset))

        return LinearCombinationAsset(terms)

    elif string.startswith("PriceySatisfiedByAsset("):
        end = find_matching_paren(string, string.index("("))
        args = parse_arguments(string[23:end])
        target = json.loads(args[0])
        stop_time = parse_fraction(args[1])
        price = parse_fraction(args[2])
        return PriceySatisfiedByAsset(target, stop_time, price)

    elif string.startswith("PriceyTimeRemainingAsset("):
        end = find_matching_paren(string, string.index("("))
        args = parse_arguments(string[25:end])
        target = json.loads(args[0])
        break_even_time = parse_fraction(args[1])
        stop_time = parse_fraction(args[2])
        max_loss = parse_fraction(args[3])
        return PriceyTimeRemainingAsset(
            target, break_even_time, stop_time, max_loss
        )

    else:
        raise ValueError(f"Unknown asset type in string: {string}")
