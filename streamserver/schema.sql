/*****************
   Drop Tables
*****************/
drop table if exists mediafiles;
drop table if exists artists;
drop table if exists albums;
drop table if exists genres;
drop table if exists years;
drop table if exists users;
/*****************
   Create Tables
*****************/
create table artists (
  id integer primary key autoincrement,
  artist text not null
);
create table years (
  year integer primary key
);
create table albums (
  id integer primary key autoincrement,
  album text not null,
  artistid integer,
  years integer,
  foreign key (artistid) references artists(id),
  foreign key (years) references years(year)
);
create table genres (
  id integer primary key autoincrement,
  genre text not null
);

create table mediafiles (
  id integer primary key autoincrement,
  filename text not null,
  fullpath text not null,
  directory text not null,
  size integer not null,
  format text not null,
  bitrate text not null,
  tn integer,
  track text,
  genreid integer,
  artistid integer,
  albumid integer,
  year integer,
  comment text,
  foreign key (genreid) references genres(id),
  foreign key (artistid) references artists(id),
  foreign key (albumid) references albums(id),
  foreign key (year) references years(year)
);
create table users (
  id integer primary key autoincrement,
  username text not null,
  passwordhash text not null,
  isadmin integer not null,
  settings text not null
);