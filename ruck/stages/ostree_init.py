import pathlib

from ruck.stages.base import OstreeBase
from ruck import utils

class OstreeInitPlugin(OstreeBase):
    def preflight_check(self):
        self.logging.info("Creating ostree repository.")
        self.repo = pathlib.Path(self.config.options.repo)

    def run(self):
        if self.repo.exists():
            self.logging.error(f"{self.repo} already exists, skipping.")
            return

        self.logging.info(f"Createing {self.repo}.")
        utils.run_command(
            ["ostree", "init", "--repo", self.repo])

    def post_install(self):
        pass
