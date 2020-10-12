# coding: utf-8

"""
    Kubernetes

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)

    OpenAPI spec version: v1.14.4
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from pprint import pformat
from six import iteritems
import re


class V1LabelSelector(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'match_expressions': 'list[V1LabelSelectorRequirement]',
        'match_labels': 'dict(str, str)'
    }

    attribute_map = {
        'match_expressions': 'matchExpressions',
        'match_labels': 'matchLabels'
    }

    def __init__(self, match_expressions=None, match_labels=None):
        """
        V1LabelSelector - a model defined in Swagger
        """

        self._match_expressions = None
        self._match_labels = None
        self.discriminator = None

        if match_expressions is not None:
          self.match_expressions = match_expressions
        if match_labels is not None:
          self.match_labels = match_labels

    @property
    def match_expressions(self):
        """
        Gets the match_expressions of this V1LabelSelector.
        matchExpressions is a list of label selector requirements. The requirements are ANDed.

        :return: The match_expressions of this V1LabelSelector.
        :rtype: list[V1LabelSelectorRequirement]
        """
        return self._match_expressions

    @match_expressions.setter
    def match_expressions(self, match_expressions):
        """
        Sets the match_expressions of this V1LabelSelector.
        matchExpressions is a list of label selector requirements. The requirements are ANDed.

        :param match_expressions: The match_expressions of this V1LabelSelector.
        :type: list[V1LabelSelectorRequirement]
        """

        self._match_expressions = match_expressions

    @property
    def match_labels(self):
        """
        Gets the match_labels of this V1LabelSelector.
        matchLabels is a map of {key,value} pairs. A single {key,value} in the matchLabels map is equivalent to an element of matchExpressions, whose key field is \"key\", the operator is \"In\", and the values array contains only \"value\". The requirements are ANDed.

        :return: The match_labels of this V1LabelSelector.
        :rtype: dict(str, str)
        """
        return self._match_labels

    @match_labels.setter
    def match_labels(self, match_labels):
        """
        Sets the match_labels of this V1LabelSelector.
        matchLabels is a map of {key,value} pairs. A single {key,value} in the matchLabels map is equivalent to an element of matchExpressions, whose key field is \"key\", the operator is \"In\", and the values array contains only \"value\". The requirements are ANDed.

        :param match_labels: The match_labels of this V1LabelSelector.
        :type: dict(str, str)
        """

        self._match_labels = match_labels

    def to_dict(self):
        """
        Returns the model properties as a dict
        """
        result = {}

        for attr, _ in iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """
        Returns the string representation of the model
        """
        return pformat(self.to_dict())

    def __repr__(self):
        """
        For `print` and `pprint`
        """
        return self.to_str()

    def __eq__(self, other):
        """
        Returns true if both objects are equal
        """
        if not isinstance(other, V1LabelSelector):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
