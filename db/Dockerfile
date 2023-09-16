FROM mariadb:11.1.2-jammy

ADD my.cnf /etc/mysql/conf.d
RUN chmod -R 444 /etc/mysql/conf.d

ADD init-database.sql /docker-entrypoint-initdb.d/init-database.sql
