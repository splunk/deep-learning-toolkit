# Configure Users and Roles

DLTK uses [Splunk's role-based access control system](https://docs.splunk.com/Documentation/Splunk/8.0.6/Security/Aboutusersandroles).

A regular Splunk user (a user importing the built-in `user` role) can open DLTK dashboards, but cannot change/manage anything nor execute algorithms. A Splunk admin user (a user importing the built-in `admin` role) can has the same DLTK capabilities as the `dltk_admin` role.

DLTK adds the following roles:

- `dltk_user`
- `dltk_engineer` (imports `dltk_user` role)
- `dltk_admin` (imports `dltk_engineer` role)

Users in the `dltk_user` role can execute DLTK algorithms. Users in the `dltk_engineer` role can create, delete and configure DLTK algorithms and deploy algorithms to environments. Users in the `dltk_admin` role can create, delete and configure DLTK environments and configure DLTK system-level objects.

Depending on what the users of your Splunk environment should be able to do, make sure the corresponding Splunk user objects import one of the above DLTK roles.

The following describes how to assign a DLTK role to an existing Splunk user:

1. Open the Splunk web interface
2. Click on *Settings* in the top Splunk bar
3. Click on *Users* in the *Users and Authentication* section
4. Identify the user that you want to assign a DLTK role to
5. Click on *Edit* in the *Actions* table column
6. Assign roles by clicking on the DLTK role name (`dltk_user`, `dltk_engineer` or `dltk_admin`) in the list of *Available item(s)* to make sure they appear in the list of *Selected item(s)*
7. Click *Save*
