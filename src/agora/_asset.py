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


class TimeProvenAsset(Asset):
    """
    The first time the target is proven, or stop_time if not proven by then.
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
                return ConstantAsset(proven_time)

        if watermark_time > self.stop_time:
            return ConstantAsset(self.stop_time)

        return self

    def lower_bound(self, watermark_time: Fraction) -> Fraction:
        return watermark_time

    def upper_bound(self, watermark_time: Fraction) -> Fraction:
        return self.stop_time


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


class PayForQuickProofAsset(Asset):
    """
    The idea of this asset is that the holder would benefit from
    seeing the target statement proven as quickly as possible.
    The holder agrees to pay some reward in exchange for being paid at some
    constant payout_rate starting at start_time and ending when the target is satisfied
    (or when some backstop_time is hit). By making
    payout_rate * (backstop_time - start_time) > reward, the holder can ensure that if
    other parties don't even attempt to prove the theorem, the holder will make a profit.
    The exact value of this asset is:
      payout_rate * max(time_proven(target, backstop_time) - start_time, 0) - reward
    = max(payout_rate * time_proven(target, backstop_time) - payout_rate * start_time - reward, -reward)
    """

    def __init__(
        self,
        target: str,
        payout_rate: Fraction,
        start_time: Fraction,
        backstop_time: Fraction,
        reward: Fraction,
    ):
        assert payout_rate >= 0, "payout_rate must be >= 0"
        assert backstop_time >= start_time, "backstop_time must be at least start_time"
        assert reward >= 0, "reward must be >= 0"

        self.target = target
        self.payout_rate = payout_rate
        self.start_time = start_time
        self.backstop_time = backstop_time
        self.reward = reward

        self._explicit_form = MaxAsset(
            [
                LinearCombinationAsset(
                    [
                        (payout_rate, TimeProvenAsset(target, backstop_time)),
                        (
                            Fraction(1),
                            ConstantAsset(-payout_rate * start_time - reward),
                        ),
                    ]
                ),
                ConstantAsset(-reward),
            ]
        )

    @property
    def explicit_form(self) -> MaxAsset:
        return self._explicit_form

    def referenced_target_ids(self) -> Set[str]:
        return {self.target}

    def simplify(
        self, target_success: TargetSuccess, watermark_time: Fraction
    ) -> Asset:
        assert self.referenced_target_ids().issubset(target_success.keys())

        simplified_explicit_form = self.explicit_form.simplify(
            target_success, watermark_time
        )

        if isinstance(simplified_explicit_form, ConstantAsset):
            return simplified_explicit_form

        return self

    def lower_bound(self, watermark_time: Fraction) -> Fraction:
        return self.explicit_form.lower_bound(watermark_time)

    def upper_bound(self, watermark_time: Fraction) -> Fraction:
        return self.explicit_form.upper_bound(watermark_time)


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

    elif isinstance(asset, TimeProvenAsset):
        return f"TimeProvenAsset({json.dumps(asset.target)},{fraction_to_str(asset.stop_time)})"

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

    elif isinstance(asset, PayForQuickProofAsset):
        return (
            f"PayForQuickProofAsset({json.dumps(asset.target)},"
            f"{fraction_to_str(asset.payout_rate)},"
            f"{fraction_to_str(asset.start_time)},"
            f"{fraction_to_str(asset.backstop_time)},"
            f"{fraction_to_str(asset.reward)})"
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

    elif string.startswith("TimeProvenAsset("):
        end = find_matching_paren(string, string.index("("))
        args = parse_arguments(string[16:end])
        target = json.loads(args[0])
        stop_time = parse_fraction(args[1])
        return TimeProvenAsset(target, stop_time)

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

    elif string.startswith("PayForQuickProofAsset("):
        end = find_matching_paren(string, string.index("("))
        args = parse_arguments(string[22:end])
        target = json.loads(args[0])
        payout_rate = parse_fraction(args[1])
        start_time = parse_fraction(args[2])
        backstop_time = parse_fraction(args[3])
        reward = parse_fraction(args[4])
        return PayForQuickProofAsset(
            target, payout_rate, start_time, backstop_time, reward
        )

    else:
        raise ValueError(f"Unknown asset type in string: {string}")
