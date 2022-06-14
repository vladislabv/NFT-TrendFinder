db.createUser(
    {
        user  : "dataviewer",
        pwd   : "Capybara123",
        roles : [
            {
                role : "read",
                db   : "nft-finder"
            }
        ]
    }
);
db.createUser(
    {
        user  : "dataworker",
        pwd   : "Wednesday17",
        roles : [
            {
                role : "readWrite",
                db   : "nft-finder"
            },
            {
                role : "dbAdmin",
                db   : "nft-finder"
            }
        ]
    }
);