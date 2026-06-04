from datawatcher.domains.base_plugin import (
    BaseDomainPlugin
)

from datawatcher.domains.timeseries.audits.timestamp_gap_audit import (
    TimestampGapAudit
)

from datawatcher.domains.timeseries.audits.duplicate_timestamp_audit import (
    DuplicateTimestampAudit
)

from datawatcher.domains.timeseries.audits.future_date_audit import (
    FutureDateAudit
)

from datawatcher.domains.timeseries.audits.time_order_audit import (
    TimeOrderAudit
)

from datawatcher.domains.timeseries.audits.frequency_consistency_audit import (
    FrequencyConsistencyAudit
)

class TimeseriesPlugin(
    BaseDomainPlugin
):

    domain_name = "timeseries"

    def register_audits(
        self,
        registry
    ):

        registry.register(
        TimestampGapAudit()
        )

        registry.register(
         DuplicateTimestampAudit()
        )

        registry.register(
        FutureDateAudit()
        )

        registry.register(
        TimeOrderAudit()
        )

        registry.register(
        FrequencyConsistencyAudit()
        )