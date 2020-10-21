# Connect to Environments

*Environments* are part of the core concept of DLTK. In order to deploy and use an *Algorithm*, it must be deployed to an *Environment*. If you want to learn more about these core concepts, please see the [Core Concepts](../../user/core/README.md) in the User Guide.

The following steps describe how to create a new DLTK *Environment*:

1. Open the Splunk web interface
2. Open the *Deep Learning Toolkit for Splunk* app
3. Click on *Configuration* and then *Environments* in the navigation bar
4. Click the *Create New Environment* button (upper right corner of the dashboard)
5. Enter a name for the new *Environment*
6. Select a *Connector* (once selected, additional fields will appear)
7. **Important:** Populate some of the additional fields, please see [Kubernetes](kubernetes.md) for details
8. Click on *Save* button

Next, validate the *Environment* settings, by following steps to deploy one of the built-in *Algorithms* into the new *Environment*:

1. Click on *Algorithms* DLTK in the navigation bar
2. Identify *Named Entity Recognition and Extraction* in the list and click on *Add Deployment* in the menu on the *Actions* column on the very right
3. Select the new *Environment* (once selected, additional fields will appear)
4. If required, populate some of the additional fields
5. Click the *Create* button - a spinning wheel indicated that the algorithms is being deployed
6. Ideally, things go well and a green checkmark icon appears - otherwhich a red icon indicates a problem (click on the status icon to show the deployment logs)
7. To see the *Algorithm* in action, open the example dashboard from navigation bar (*Examples* -> *NLP* -> *Entity Recognition and Extraction Example using the spaCy Library*)
