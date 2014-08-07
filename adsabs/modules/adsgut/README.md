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

### odd corners

#### members in tags