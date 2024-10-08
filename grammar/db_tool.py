from langchain import SQLDatabase
from langchain.tools.sql_database.tool import QuerySQLDataBaseTool
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.sql.sqltypes import Date, DateTime, Time
from typing import List


def check_relevant_table(table_name, entity_types):
    entity_types = [entity_type.lower() for entity_type in entity_types]
    # check if the table is relevant to the entity types
    relevant = False
    if table_name.lower() in entity_types:
        relevant = True

    # check if the table name contains any entity type
    count_table = 0
    for entity_type in entity_types :
        if entity_type in table_name.lower() :
            count_table += 1
        if count_table >= 2:
            relevant = True
            break
    return relevant

class DBTool:
    def __init__(self, connection_string) -> None:
        
        self.engine = create_engine(connection_string)
        self.metadata = MetaData()
        self.metadata.reflect(bind=self.engine,)

        # for query (TODO: decouple this from langchain)
        self.langchain_db = SQLDatabase.from_uri(connection_string, sample_rows_in_table_info=0)
        # self.query_sql_database_tool = QuerySQLDataBaseTool(db=db)
        # query table names and schema
        # table_names = ", ".join(db.get_usable_table_names())
        # schema = db.get_table_info(table_names.split(", ")) # create table commands

    def query(self, sql):
        return self.langchain_db.run_no_throw(sql)
        # return self.engine.execute(query)
    
    def infer_entity_types_from_table_names(self, verbose=False):
        
        table_names = list(self.metadata.tables.keys())
        # remove associative tables with "_" to connect two table names
        table_names = [name for name in table_names if "_" not in name]
        return table_names
    
    def get_table_schema(self, table_or_table_name):
        """ Schema of a table
            Args:
                table_or_table_name (str or Table): the table object or the table name
            
            Returns:
                schema (Tuple[str, List[Dict]]): the table name and the columns
        """
        table = table_or_table_name
        if isinstance(table_or_table_name, str):
            table = Table(table_or_table_name, self.metadata, autoload=True, autoload_with=self.engine)
        columns = []
        for column in table.columns:
            column_info = {}
            column_info['name'] = column.name
            column_info['type'] = str(column.type)
            column_info['nullable'] = column.nullable
            column_info['primary_key'] = column.primary_key
            columns.append(column_info)
            # column_info['default'] = column.default
            # column_info['autoincrement'] = column.autoincrement
            # column_info['comment'] = column.comment
            # column_info['foreign_keys'] = list(column.foreign_keys)
        return (table.name, columns)

    @property
    def db_schema(self):
        """ Schema of the database
            Returns:
                schema (List[Tuple[str, List[Dict]]]): a list of tuples, each tuple contains the table name and the columns
        """
        schema = []
        for table in self.metadata.sorted_tables:
            schema.append(self.get_table_schema(table))
        return schema

    def get_date_columns(self, table_name):

        table = Table(table_name, self.metadata, autoload=True, autoload_with=self.engine)
        return [column.name for column in table.columns if isinstance(column.type, (Date, DateTime, Time))]
    
    def infer_schema_from_entity_types(self, entity_types: List[str]):
        """Get the schema for the given entity types. 
            Args:
                entity_types (List[str]): a list of entity types
            
            Returns:
                schema (List[Tuple[str, List[Dict]]]): a list of tuples, each tuple contains the table name and the columns
            """
        assert isinstance(entity_types, (list, tuple)), "`entity_types` must be a list or tuple"
        schema = []
        
        for table_name, columns in self.db_schema:
            if not check_relevant_table(table_name, entity_types):
                continue
            schema.append((table_name, columns))
        return schema

    def stringify_schema(self, schema=None):
        """Stringify the schema for the given entity types. 
            Args:
                schema (List[Tuple[str, List[Dict]]]): a list of tuples, each tuple contains the table name and the columns
            
            Returns:
                schema_str (str): a string representation of the schema
            """
        if schema is None:
            schema = self.db_schema
        schema_str = ""
        for table_name, columns in schema:
            schema_str += f"Table: {table_name}\n"
            for column in columns:
                schema_str += f"\t Column: {column['name']} ({column['type']})\n"
        return schema_str