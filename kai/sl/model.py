from kai.aiml.model import AimlBinding
from kai.cassandra.model import ATResult
from kai.utility.utils import current_datetime_as_string


# convert an AIml binding to an ATResult
def convert_aiml_binding(binding: AimlBinding) -> ATResult:
    return ATResult(binding.text, current_datetime_as_string(), binding.origin)
