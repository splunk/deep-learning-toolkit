from dltk.core import execution
from dltk.connector.kubernetes import KubernetesExecution
import urllib
import http
import json

__all__ = ["BaseExecution"]


class BaseExecution(KubernetesExecution):

    def handle(self, buffer, finished):

        base_url = self.deployment.runtime_status["api_url"]
        if self.context.method.name == "fit":
            url = urllib.parse.urljoin(base_url, "fit")
        elif self.context.method.name == "apply":
            url = urllib.parse.urljoin(base_url, "apply")
        elif self.context.method.name == "summary":
            url = urllib.parse.urljoin(base_url, "summary")
        else:
            raise Exception("unsupported method")

        content = {
            "data": ','.join(self.context.fields) + "\n" + buffer.decode(),
            "meta": {},
        }
        request = urllib.request.Request(
            url,
            method="POST",
            data=json.dumps(content).encode(),
            headers={
                "Content-Type": "application/json",
            }
        )
        response = urllib.request.urlopen(request)

        self.logger.warning("sent %s bytes" % len(buffer))

        return execution.ExecutionResult(
            events=[],
        )
