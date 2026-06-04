from datawatcher.domains.base_plugin import (
    BaseDomainPlugin
)

from datawatcher.domains.finance.audits.negative_value_audit import (
    NegativeValueAudit
)

from datawatcher.domains.finance.audits.currency_consistency_audit import (
    CurrencyConsistencyAudit
)

from datawatcher.domains.finance.audits.interest_rate_audit import (
    InterestRateAudit
)

from datawatcher.domains.finance.audits.balance_consistency_audit import (
    BalanceConsistencyAudit
)

class FinancePlugin(
    BaseDomainPlugin
):

    domain_name = "finance"

    def register_audits(
        self,
        registry
    ):

        registry.register(
            NegativeValueAudit()
        )

        registry.register(
            CurrencyConsistencyAudit()
        )

        registry.register(
        InterestRateAudit()
        )

        registry.register(
        BalanceConsistencyAudit()
        )