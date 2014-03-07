/*****************
   Drop Tables
*****************/
drop table if exists mediafiles;
drop table if exists artists;
drop table if exists albums;
drop table if exists genres;
drop table if exists years;
drop table if exists users;
drop table if exists directories;
drop table if exists files;
/*****************
   Create Tables
*****************/
create table artists (
  id integer primary key autoincrement,
  artist text not null unique
);
/*create table years (
  year integer primary key
);*/
create table albums (
  id integer primary key autoincrement,
  album text not null unique, /*todo:deal with it*/
  artistid integer not null,
  foreign key (artistid) references artists(id)
);
create table genres (
  id integer primary key autoincrement,
  genre text not null unique
);

create table mediafiles (
  id integer primary key autoincrement,
  filename text not null ,
  fullpath text not null unique,
  directory text not null,
  parentid integer,
  size text not null,
  format text not null,
  length text not null,
  bitrate text not null,
  tn integer,
  title text,
  genreid integer,
  artistid integer,
  albumid integer,
  year text,
  comment text,
  foreign key (genreid) references genres(id),
  foreign key (artistid) references artists(id),
  foreign key (albumid) references albums(id)/*,
  foreign key (year) references years(year)*/
);
create table users (
  id integer primary key autoincrement,
  username text not null,
  passwordhash text not null,
  isadmin integer not null,
  settings text not null
);
create table directories (
  id integer primary key,
  parentid integer not null,
  directory text not null
);
/******************************
INSERT user: admin
       that hash is for 'pass'
*******************************/

INSERT INTO users VALUES(1,'admin','3cc7506c9f6a7525e21d92009eeb9fef87c67f4e8fa4b05e8a8e80c1857d10f048fec3645fe0795bb02f514b8cacf88ab3fd6b920041c0e19ee3509471fb8fdc',1,'');