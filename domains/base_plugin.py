from abc import ABC
from abc import abstractmethod


class BaseDomainPlugin(ABC):

    domain_name = None

    @abstractmethod
    def register_audits(
        self,
        registry
    ):
        pass