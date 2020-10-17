


[<algorithm_name>]

runtime = <string>
* Name of the DLTK runtime which is used for the algorithm to execute in.
* Required.

description = <string>
* Description of the algorithm which also appears in the algorithms overview UI
* Optional.

category = <string>
* Algorithm category name. For example 'Clustering', 'Classifier', 'Regressor', ...
* Optional.

max_buffer_size = [auto|all|<number_of_bytes>]
* Maximum number of bytes DLTK buffers data received by splunkd as during each DLTK algorithm execution.
* In case the DLTK command runs in 'streaming' mode (or in 'reporting' mode with 'streaming' pre-op), this applies for all search peers (this also includes the search head itself) independently.
* In addition (for 'streaming' and non-'streaming' commands), this also applies for initiating search head.
* A value of 'auto' simply passes each chunk received by splunkd to the DLTK exection handler.
* A value of 'all' buffers all chunks and calls the execution handle just once (possibly per search peer and search head).
* An empty attribute default to 'auto'
* Defaults to 'auto'

command_type = [streaming|stateful|events|reporting]
* streaming: one-by-one, can be pushed to indexers
* stateful: one-by-one, sh-only, no re-ordering
* events: sh-only, may re-order
* reporting: sh-only, for stats/etc
* See https://docs.splunk.com/Documentation/Splunk/latest/Search/Typesofcommands for details.
* You may also have a look at https://conf.splunk.com/files/2017/slides/extending-spl-with-custom-search-commands-and-the-splunk-sdk-for-python.pdf
* Defaults to 'reporting'

support_preop = <boolean>
* Whether or not to support 'streaming' pre-op for 'reporting' commands
* Defaults to false.

source_code = <string>
* Contains the source code of the algorithm
* As example this can be a ipynb jupyter notebook json code or python code or any other source code
* Optional.

deployment_code = <string>
* Optional.


[<algorithm_name>:<method_name>]

max_buffer_size = [auto|all|<number_of_bytes>]
* Defaults to what is set to 'max_buffer_size' the algorithm stanza.

command_type = [streaming|stateful|events|reporting]
* Defaults to what is set to 'command_type' the algorithm stanza.

support_preop = <boolean>
* Defaults to what is set to 'support_preop' the algorithm stanza.

