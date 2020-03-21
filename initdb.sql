
-- Nyt periaatteessa monelle käyttäjälle voi
-- laittaa saman faktan helposti, onko hyödyllistä,
-- ei voi tietää

-- mahdollistaa myös satunnaisen käyttäjän sekä faktan yhdistämisen
create table users(
    id integer primary key autoincrement,
    name text
);

create table fact(
    id integer primary key autoincrement,
    fact text
);


create table person_facts(
    userid integer,
    factid integer,
    foreign key(userid) references user(id),
    foreign key(factid) references fact(id)
);



