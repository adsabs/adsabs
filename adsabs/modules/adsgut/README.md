#ADSGUT

##What is ADSGUT?

ADSGUT is a subsystem of ads 2.0, whose job is to run the social aspects of the ADS site.

What does this mean? It means, that once the user has logged in, it must
(a) enable the user to save a search
(b) enable the user to save a set of publications in a "library"
(c) allow a user to tag these publications, and make notes on them
(d) allow a library to be associated with a group and shared with other groups.

These are the concepts:
(a) library: a collection of papers. each user has a default library userid/library:default . A library is associated with every group. A library can have both users and groups as members. A user's access to a library may be read-only or
read-write. If there are multiple ways a user is in a library (directly, through multiple groups), the read-write is associated with the most permissive belonging.
(b) a user, who has a 1-1 correzpondence to the ADS identity database. A user is represented by an adsid, which
is the user's email, a userid which is a 128 bit uuid
(c) group: a group to which a user belongs. adsgut/group:public is the Public group.
Everyone belongs to this group. A group has an owner, a user. There is a library associated with each group; 
library may have other groups or users as members.
(d) app: an app is a special collection of users and groups. The idea is to allow third party apps, but currently we only have the mothership app and the flagship ads app. Apps are currently used to mediare access to itemtypes and tagtypes.
Being a member of the app under which an itemtype or tagtype is defined allows for access to that itemtype and tagtype.
All users are members of thee publications app which gives then access to the publications itemtype and the tag and note tagtypes.