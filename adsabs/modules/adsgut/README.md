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
All users are members of the publications app which gives then access to the publications itemtype and the tag and note tagtypes.

Now we get to the concepts which have to do with publishing:

(a) itemtypes and tagtypes: so far, pubs, searches, tags, and notes.
(b) items are posted using 'PostingDocuments' to a library.
(c) tags: a wword tag like "lensing" or a note whith tagname as a uuid and description or content. The latter kind of
tag has singletonmode=True. We havent defined other tags and note like things as yet, but we could use this functionality
to define tag systems. Tags have members as well, which is a quick way to keep track of who can access the tag.
(d) the act of tagging, as defined in taggingdocument, adds a tagmode. The tagmode default is defined in the tagtype
class, but can be overrode in the tagging. The choices are '0':promiscuous, the tagging is spread to all the libraries, an item is in , '1', private,where it goes only to the user default library, and fqpn, which adds the fully qualified name of the library the tag should be posted in.