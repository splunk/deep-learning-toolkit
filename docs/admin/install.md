# Installing Deep Learning Toolkit for Splunk

The Deep Learning Toolkit for Splunk is a regular Splunk app which runs on a Splunk Search Head. That may be a standlone Search Head or a Search Head Cluster.

If you want to learn more about setting up a Splunk environment, please see the official [Splunk Installation Manual](https://docs.splunk.com/Documentation/Splunk/latest/Installation).

Currently, DLTK v4 is still under development and **not yet** released on [Splunkbase](https://splunkbase.splunk.com/). But you can install DLTK v4 from this repository. The Splunk app itself is located in the [`app`](../../app/) folder, in the root of this repository.

Depending on the deployment type of your Splunk environment (standlone Search Head vs. Search Head cluster) as well as your preferred app deployment method (Deployment Server vs. Upload via Splunk Web vs. Search Head Deployer vs. 3rd Party Deployment Software), you either use a copy of the `app` folder as it is, or you create an app package (using tools like [tar](https://en.wikipedia.org/wiki/Tar_(computing)), [gzip](https://en.wikipedia.org/wiki/Gzip) or [slim]( https://dev.splunk.com/enterprise/docs/releaseapps/packagingtoolkit/pkgtoolkitref/packagingtoolkitcli#slim-package)). To learn more about the methods to deploy Splunk apps in Splunk Enterprise environments, please see the [App Deployment](https://docs.splunk.com/Documentation/Splunk/latest/Admin/Deployappsandadd-ons) documentation.

The following illustrates the installation process on a standalone Splunk Search Head or single-instance Splunk environment:

```bash
git clone https://github.com/splunk/deep-learning-toolkit.git
cd deep-learning-toolkit
cp -r app/ $SPLUNK_HOME/etc/apps/dltk
$SPLUNK_HOME/bin/splunk restart
```

Once installed, you can navigate to the *Deep Learning Toolkit for Splunk* in the Splunk web interface.

Next, please see the [Configure Users and Roles](access_control.md) documentation.
