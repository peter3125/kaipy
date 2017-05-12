/////////////////////////////////////////////
// users and sessions

create table if not exists <ks>.user (
        email text, first_name text, surname text, salt uuid, password_hash text,
        primary key(email)
);

create table if not exists <ks>.session (
        email text, first_name text, surname text, session uuid,
        primary key(session)
);

/////////////////////////////////////////////
// log action table

create table if not exists <ks>.logs (
	when bigint, who text, what text,
	primary key(when)
);

/////////////////////////////////////////////
// generic inverted index: word -> url.  The word_origin is the base of the relationship expansion
// offset is WHERE the word is.  kb is what part of the system this knowledge is from

create table if not exists <ks>.word_index (
    word text, tag text, shard int, sentence_id uuid, offset int, topic text, score double,
    primary key((word, shard), topic, sentence_id, offset, tag)
);

// remove indexes, given a url, get the words indexed for that url
create table if not exists <ks>.word_unindex (
    sentence_id uuid, word text, shard int,
    primary key((sentence_id), word, shard)
);

/////////////////////////////////////////////
// sentence and topics

create table if not exists <ks>.sentence_by_topic (
    id uuid, topic text,
    primary key((topic), id)
);

create table if not exists <ks>.sentence_by_id (
    id uuid, topic text, json_data text,
    primary key(id)
);

