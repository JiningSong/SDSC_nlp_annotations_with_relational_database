from inserter import Inserter


if __name__ == "__main__":

    # Specify path to config file
    path_to_configfile = "config.ini"

    # Create an Inserter
    inserter = Inserter(path_to_configfile)

    # Start insertion from src file to database (both are specified in config file)
    inserter.start_insertion()
