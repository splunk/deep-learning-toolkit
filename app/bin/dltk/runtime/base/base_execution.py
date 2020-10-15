from dltk.core import execution
from dltk.connector.kubernetes import KubernetesExecution
import urllib
import http
import json
import io

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

        # include a header and only keep the first len(self.context.fields) values
        field_count = len(self.context.fields)
        clean_buffer = io.BytesIO()
        clean_buffer.write((','.join(self.context.fields) + "\n").encode())
        while buffer.readable():
            line = buffer.readline()
            if not line:
                break
            clean_buffer.write(line[:-(field_count + 1)] + b"\n")
        buffer_bytes = clean_buffer.getvalue()

        self.logger.warning("sending %s bytes" % len(buffer_bytes))

        content = {
            "data": buffer_bytes.decode(),
            "meta": {
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
        returns = response.read()

        result = json.loads(returns.decode())
        if not "status" in result:
            return execution.ExecutionResult(error="No status found in container results")
        status = result['status']
        if status == "error":
            return execution.ExecutionResult(error=result['message'])

        self.logger.warning("returns %s" % str(returns))

        return execution.ExecutionResult(
            events=result['results'],
        )
