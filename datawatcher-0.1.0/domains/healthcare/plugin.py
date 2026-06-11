from datawatcher.domains.base_plugin import (
    BaseDomainPlugin
)

from datawatcher.domains.healthcare.audits.age_range_audit import (
    AgeRangeAudit
)

from datawatcher.domains.healthcare.audits.bmi_range_audit import (
    BMIRangeAudit
)

from datawatcher.domains.healthcare.audits.blood_pressure_audit import (
    BloodPressureAudit
)

from datawatcher.domains.healthcare.audits.heart_rate_audit import (
    HeartRateAudit
)

from datawatcher.domains.healthcare.audits.lab_result_range_audit import (
    LabResultRangeAudit
)

from datawatcher.domains.healthcare.audits.missing_diagnosis_audit import (
    MissingDiagnosisAudit
)

from datawatcher.domains.healthcare.audits.medication_consistency_audit import (
    MedicationConsistencyAudit
)

class HealthcarePlugin(
    BaseDomainPlugin
):

    domain_name = "healthcare"

    def register_audits(
        self,
        registry
    ):

        registry.register(
            AgeRangeAudit()
        )

        registry.register(
            BMIRangeAudit()
        )

        registry.register(
            BloodPressureAudit()
        )

        registry.register(
        HeartRateAudit()
        )

        registry.register(
        LabResultRangeAudit()
        )

        registry.register(
        MissingDiagnosisAudit()
        )

        registry.register(
        MedicationConsistencyAudit()
        )