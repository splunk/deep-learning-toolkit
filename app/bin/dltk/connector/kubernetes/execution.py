from dltk.core import execution


class KubernetesExecution(execution.Execution):

    def generate_object_name_suffix(self, suffix=None):
        if suffix:
            return "%s-%s" % (
                self.deployment.generate_label_value(self.context.search_id),
                suffix,
            )
        else:
            return self.deployment.generate_label_value(self.context.search_id)

    def get_object_labels(self, labels={}):
        labels.update({
            "search_id": self.deployment.generate_label_value(self.context.search_id),
        })
        return labels

    def finalize(self):
        if not self.context.is_preop:
            self.deployment.delete_objects(
                only_outdated=False,
                include_services=True,
                include_workloads=True,
                include_volumes=True,
                include_secrets=True,
                include_ingresses=True,
                additional_label_selector=self.get_object_labels(),
            )
