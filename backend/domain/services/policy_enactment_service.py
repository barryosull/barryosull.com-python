from backend.domain.entities.game_state import GameState
from backend.domain.value_objects.policy import Policy, PolicyType


class PolicyEnactmentService:
    @staticmethod
    def draw_policies(game_state: GameState) -> list[Policy]:
        return game_state.policy_deck.draw(3)

    @staticmethod
    def president_discards_policy(
        policies: list[Policy], discarded_policy: Policy
    ) -> list[Policy]:
        if len(policies) != 3:
            raise ValueError("President must have exactly 3 policies")

        if not any(p is discarded_policy for p in policies):
            raise ValueError("Discarded policy must be one of the drawn policies")

        policies.remove(discarded_policy)
        return policies

    @staticmethod
    def chancellor_enacts_policy(
        game_state: GameState, policies: list[Policy], enacted_policy: Policy
    ) -> Policy:
        if len(policies) != 2:
            raise ValueError("Chancellor must have exactly 2 policies")

        if not enacted_policy in policies:
            raise ValueError("Enacted policy must be one of the available policies")

        discarded = [p for p in policies if p is not enacted_policy]

        game_state.policy_deck.discard(discarded)

        if enacted_policy.type == PolicyType.LIBERAL:
            game_state.enact_liberal_policy()
        else:
            game_state.enact_fascist_policy()

        return enacted_policy

    @staticmethod
    def enact_chaos_policy(game_state: GameState) -> Policy:
        policies = game_state.policy_deck.draw(1)
        enacted_policy = policies[0]

        if enacted_policy.type == PolicyType.LIBERAL:
            game_state.enact_liberal_policy()
        else:
            game_state.enact_fascist_policy()

        return enacted_policy
