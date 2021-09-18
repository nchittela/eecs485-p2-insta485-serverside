PRAGMA foreign_keys = ON;

CREATE TABLE users(
  username VARCHAR(20) NOT NULL,
  fullname VARCHAR(40) NOT NULL,
  email VARCHAR(40) NOT NULL, 
  filename VARCHAR(64) NOT NULL,
  password VARCHAR(256) NOT NULL,
  created TIMESTAMP DEFAULT DATETIME('now')
  PRIMARY KEY(username)
);

CREATE TABLE posts(
  postid INTEGER AUTOINCREMENT,
  filename VARCHAR(64) NOT NULL, 
  owner VARCHAR(20) NOT NULL,
  created TIMESTAMP DEFAULT DATETIME('now'),
  PRIMARY KEY(postid),
  FOREIGN KEY (owner) REFERENCES users(owner) ON DELETE CASCADE
);

CREATE TABLE following(
  username1 VARCHAR(20) NOT NULL,
  username2 VARCHAR(20) NOT NULL,
  PRIMARY KEY (username1, username2),
  FOREIGN KEY (username1) REFERENCES users(username1) ON DELETE CASCADE,
  FOREIGN KEY (username2) REFERENCES users(username2) ON DELETE CASCADE
);

CREATE TABLE comments(
  commentid INTEGER AUTOINCREMENT,
  owner VARCHAR(20) NOT NULL,
  postid INTEGER NOT NULL,
  text VARCHAR(1024) NOT NULL,
  created TIMESTAMP DEFAULT DATETIME('now'),
  PRIMARY KEY(commentid),
  FOREIGN KEY (owner) REFERENCES users(owner) ON DELETE CASCADE,
  FOREIGN KEY (postid) REFERENCES posts(postid)
);

CREATE TABLE likes(
  likesid INTEGER AUTOINCREMENT,
  owner VARCHAR(20) NOT NULL,
  postid INTEGER NOT NULL,
  created TIMESTAMP DEFAULT DATETIME('now'),
  PRIMARY KEY(likesid),
  FOREIGN KEY (owner) REFERENCES users(owner) ON DELETE CASCADE,
  FOREIGN KEY (postid) REFERENCES posts(postid)
);