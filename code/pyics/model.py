#
# Base functionality for all models.
#
# A model may have any number of parameters, which can be changed from outside
# the model (e.g. by a GUI). Using this base a model can easily define these
# parameters, and allows both the model itself and the outside code to easily
# access them.
#
# Written by the teachers of the UvA bachelor course `Introduction Computational Science'.
#

def make_getter(name):
    """Returns a getter function which returns the attribute `name'."""
    return lambda self: getattr(self, name)


def make_setter(name, var_type, user_setter):
    """Returns a setter function which sets the attribute `name', first casting
    it to `type' and passing it through the `user_setter' function."""
    return lambda self, new_val: setattr(self, name,
            user_setter(var_type(new_val)))


class Model(object):
    """Base class for models which have a number of parameters.

    All models should inherit from this class, and should override the `reset',
    `step' and `draw' functions. Otherwise, an exception will be raised.

    A model can optionally have any number of parameters. Parameters are
    variables which influence the simulation that can be changed at-runtime
    (e.g. by a GUI). Any parameters should be registered during initialization
    of the instance using the `make_param' method."""

    def __init__(self):
        self.params = []

    def make_param(self, name, default_value, param_type=None, setter=None, range=False,
                min=0, max=0):
        """Registers a parameter for the current model.

        This method will:
        1) Register the name of the parameter in a list, `params', which can
           then be used from other code (such as a GUI) to get all parameters.
        2) Create a property with getter and setter, which then allows further
           code to use the variable as it normally would. The setter of the
           property makes sure the parameter is always the correct type and can
           optionally call a user-defined setter.

        The code can be used as follows:

            >>> class MySim(Model):
            ...     def __init__(self):
            ...         Model.__init__(self)
            ...         self.make_param('num_turtles', 5)
            ...     def reset(self):
            ...         self.turtles = []
            ...         for i in range(self.num_turtles):
            ...             self.turtles.append('turtle')

        The actual variable in which the value is stored (and which the property
        accesses) is called _param_VARNAME, and should not be used directly.
        """

        setter = setter or (lambda x: x)
        param_type = param_type or type(default_value)
        hidden_var_name = '_param_%s' % name
        self.params.append(name)
        setattr(self, hidden_var_name, setter(param_type(default_value)))
        # We have to add the property to the actual class, not the instance.
        # Luckily this keeps working fine even if we have multiple instances
        # (and thus register the same property twice etc)
        setattr(self.__class__, name,
                property(make_getter(hidden_var_name),
                         make_setter(hidden_var_name, param_type, setter)))
