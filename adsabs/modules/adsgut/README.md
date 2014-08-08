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

### namespaces

The public group `adsgut/group:public`

The library for this public group is `adsgut/library:public`

Everyone belongs to this app but it has no use: `adsgut/app:adsgut`. This is the mothership app.

Everyone belongsto the flagship app `ads/app:publications` and the use here is to make sure all have access to tags, notes
pubs and searches. it may be worth having the MOTHERSHIP app own tags and notes but this works for now.

The anonymouse user `adsgut/user:anonymouse` isused to represent a user who hasnt logged in. When u make a library public, access is given to this user, and the public group. From this point on you can toggle access for these entities individually.

The tagtype tag is represented as: `ads/tagtype:tag`.

Here is a tag: `5e412bfa-c183-4e44-bbfd-687a54f07c9c/ads/tagtype:tag:random`. Notice the user namespacing, the full
tag namespace, and then the name `random`. A note looks thus: `501e05e4-4576-4dbe-845d-876042d2d614/ads/tagtype:note:769c1d1f-a242-49cb-82ba-fbb6761ee4a8` with `description` having the content.

A user usually looks thus: `adsgut/user:501e05e4-4576-4dbe-845d-876042d2d614`

An item has a different structure: `ads/2014bbmb.book..243K`. We dont have the itentype in the
fully qualified name but the itemtype is there in the namespace. The itentype for this item is `ads/itemtype:pub`.

A group looks like `5e412bfa-c183-4e44-bbfd-687a54f07c9c/group:mine` with a library looking something like this:
`501e05e4-4576-4dbe-845d-876042d2d614/library:wolla`.



### files in mongogut

this section describes files in the mongogut repo.

The classes, that is the entire data model for the concepts given above are defined in `mongoclasses.py`. We use MongoEngine classes as our 'ORM'. We also make some common concept definitions.

These are:
	POSTABLES=[Library]#things that can be posted to
	MEMBERABLES=[Group, App, User]#things that can be members
	MEMBERABLES_NOT_USER=[Group, App]#things that can be members whih are not a user
	MEMBERABLES_FOR_TAG_NOT_USER=[Group, App, Library]#things that can be members of tags
	MEMBABLES=[Group, App, Library, Tag]#things you can be a member of
	OWNABLES=[Group, App, Library, ItemType, TagType, Tag]#things that can be owned
	OWNERABLES=[User]#things that can be owners.

In a sense, these definitions set up interfaces which are system hews too. In the course of the development of this system, we had initially concieved groups, apps, and libraries as sharing a postable and membable interface, but each being slightly different. But it soon became clear that we wanted groups to be collections of users and libraies to be the only
things one could post items into. Thus we see the current structure we have over here.

In this file we also define `MMMAP` which says who can be a member of whom, `RWDEF` which says who can post where,
In `utilities.py`, we have defined spec augmenting functions. A spec is the dictionary used to construct a mongoengine object.

In `social.py` we define a database class whose methods deal with users, libraries, groups, and apps. These concepts then are dealt with as memberables and membables. Because of the history of the system, you may see `postablesin` and `postablesowned` attributes: substitute membables in their place mentally.

In `ptassets.py` we make another database class. This database class containes methods for posting items to libraries, tagging items, a blinker based signal routing system to add tags to the appropriate libraries. It has as an instance variable the social database, and also provides multiple methods to query the items database. To get the items in a library, we query posting documents. This makes the system speedier and also gets tags and such.

There is no pagination yet; this is built into the ptassets system but is not exposed in the UI.

### files for the web services

`webservices.py` is the main file which documents all the routes in the system. `webchrome.py` is supposed to do the chrome but we have not activated this as yet.

### javascript files, coffeescript files, and templates

### odd corners

#### members in tags