# DMF Catalog
DMF stands for "Dynamic Marketing Funnel".  The application is designed to present academic degree programs in a way that can be marketed by terms like: "Business, Finance, Bible, Education".  A database of taxonomy terms enriches the ability to present Academic pages with various sorting lists.  Includes the capability to associate parents and children with a unique text code.  This parent-child relationship is used for the tiered list of children that also have marketable features, such as concentrations or licensures of program majors.

There is certainly the need to further abastract database elements and internal displays as well as reduce the dependancy on bootstrap styling.  The naming inconsistancy between DPC and DMF is apparent.  I tried to weed this out of the database but gave up as it wasn't necessary to my own uses.

Visit / for a presentation of the /demo view
See templatetags\catalog_tags for lots of notes on how blocks can be created by taxonomy terms.
See functions.py for the nuts and bolts of how parents and children are called and produced by arguments sent though custom tags

The application also includes some capabilities to import/export data