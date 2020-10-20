from dltk.core import execution
from dltk.connector.kubernetes import KubernetesExecution
import urllib
import http
import json
import io

__all__ = ["BaseExecution"]


class BaseExecution(KubernetesExecution):

    def handle_summary(self, url):
        request = urllib.request.Request(
            url,
            method="GET",
            headers={
                "Content-Type": "application/json",
            }
        )
        response = urllib.request.urlopen(request)
        returns = response.read()
        summary_result = { "summary" : str(returns.decode()) }
        return execution.ExecutionResult(
            events=[summary_result],
        )


    def handle(self, buffer, finished):

        base_url = self.deployment.runtime_status["api_url"]
        if self.context.method.name == "fit":
            url = urllib.parse.urljoin(base_url, "fit")
        elif self.context.method.name == "apply":
            url = urllib.parse.urljoin(base_url, "apply")
        elif self.context.method.name == "summary":
            url = urllib.parse.urljoin(base_url, "summary")            
            return self.handle_summary(url)         
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
                "options": {
                    "params": {
                        "algo": "algo",
                    }
                }
            },
        }
        for k, v in self.context.params.items():
            if k == "model_name":
                content["meta"]["options"]["model_name"] = v
            if k == "feature_variables" or k == "target_variables":
                v = v.split(',')
                content["meta"][k] = v
            content["meta"]["options"]["params"][k] = v

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

        return_events = []
        if "results" in result:
            return_events = result['results']

        return execution.ExecutionResult(
            events=return_events,
        )
