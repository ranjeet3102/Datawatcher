from datawatcher.domains.finance.plugin import (
    FinancePlugin
)

from datawatcher.domains.timeseries.plugin import (
    TimeseriesPlugin
)

from datawatcher.domains.healthcare.plugin import (
    HealthcarePlugin
)

DOMAIN_PLUGINS = {

    "finance":
        FinancePlugin(),

    "timeseries":
        TimeseriesPlugin(),

    "healthcare":
        HealthcarePlugin()
}