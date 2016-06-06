drop table if exists articles;
create table articles (
  id integer primary key autoincrement,
  slug text(50) not null unique,
  title text(200) not null,
  intro text not null,
  'text' text not null,
  'date' datetime not null,
  published boolean,
  description text,
  keywords text
);
