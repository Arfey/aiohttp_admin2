import pytest
import psycopg2
import pymongo
import pymysql


@pytest.fixture(scope="session")
def postgres(docker_ip, docker_services):
    """Ensure that Postgres service is up and responsive."""

    port = docker_services.port_for("postgres_test", 5432)
    data = dict(
        user='postgres',
        password='postgres',
        host=docker_ip,
        port=port,
        database='postgres',
    )

    def is_responsive(postgres_data):
        try:
            conn = psycopg2.connect(**postgres_data)
            cur = conn.cursor()
            cur.close()
            conn.close()
            return True
        except psycopg2.Error:
            return False

    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.1, check=lambda: is_responsive(data)
    )

    return data


@pytest.fixture(scope="session")
def mysql(docker_ip, docker_services):
    """Ensure that MySql service is up and responsive."""

    port = docker_services.port_for("mysql_test", 3306)
    data = dict(
        user='mysql',
        password='mysql',
        host=docker_ip,
        port=port,
        database='mysql',
    )

    def is_responsive(mysql_data):
        try:
            conn = pymysql.connect(**mysql_data)
            cur = conn.cursor()
            cur.execute("SELECT 1;")
            cur.close()
            conn.close()
            return True
        except Exception:
            return False

    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.1, check=lambda: is_responsive(data)
    )

    return data


@pytest.fixture(scope="session")
def mongo(docker_ip, docker_services):
    """Ensure that mongodb service is up and responsive."""

    port = docker_services.port_for("mongodb_test", 27017)
    data = dict(
        host=docker_ip,
        port=port,
    )

    def is_responsive(mongo_data):
        try:
            conn = pymongo.MongoClient(**mongo_data)
            conn.server_info()
            conn.close()
            return True
        except Exception:
            return False

    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.1, check=lambda: is_responsive(data)
    )

    return data
