from abc import abstractmethod


class UserFriendlyError:
    """ Provides user friendly error message. """

    @abstractmethod
    def user_friendly_message(self) -> str:
        """ Returns the user friendly error message. """
        ...