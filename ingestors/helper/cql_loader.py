import os

class CQLLoader:
    """
    This class is responsible for reading and filtering CQL commands from a given file.
    """

    def __init__(self, cql_file_path):
        """
        Initialize the CQLLoader with the path to the CQL file.

        :param cql_file_path: Path to the CQL file.
        """
        self.cql_file_path = cql_file_path

    def _read_cql_file(self):
        """
        Read the CQL file and return a list of commands separated by semicolons.

        :return: List of raw CQL commands.
        """
        with open(self.cql_file_path, 'r') as file:
            return file.read().split(';')

    def _filter_commands(self, category):
        """
        Filter CQL commands based on the given category ("Schema", "Query", "Modification").

        :param category: Category to filter by.
        :return: List of filtered CQL commands.
        """
        raw_commands = self._read_cql_file()
        
        filtered_commands = []
        
        for raw_command in raw_commands:
            # Remove comments and perform strip() on each line
            lines = [line.strip() for line in raw_command.split('\n') if not line.strip().startswith('--')]
            cleaned_command = ' '.join(lines).upper()
            
            if category == "Schema" and "CREATE TABLE" or "CREATE KEYSPACE" in cleaned_command:
                filtered_commands.append(raw_command)
            elif category == "Query" and "SELECT" in cleaned_command:
                filtered_commands.append(raw_command)
            elif category == "Modification" and cleaned_command.startswith(("INSERT", "UPDATE", "DELETE")):
                filtered_commands.append(raw_command)
                
        # print("Gefilterte Kommandos:", filtered_commands)  # Zum Debugging
        return filtered_commands


    def get_commands(self, category=None):
        """
        Public method to get the CQL commands based on the given category.

        :param category: Category to filter by (optional).
        :return: List of filtered CQL commands.
        """
        return self._filter_commands(category)


if __name__ == "__main__":

    schema_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../schema/cql/vital_params_schema.cql'))
    
    loader = CQLLoader(schema_file_path)
    schema_commands = loader.get_commands("Schema")  
    
