"""
execution_analytics_service.py

Business logic for execution analytics.

Author: Tharindu Kothalwala
Project: Aladdin
"""


class ExecutionAnalyticsService:
    """
    Provides execution statistics.
    """

    def __init__(
        self,
        repository,
    ):

        self.repository = repository

    def get_statistics(
        self,
        user_id: int,
    ):
        """
        Calculate execution statistics
        for a user.
        """

        executions = self.repository.get_user_executions(user_id)

        total_executions = len(executions)

        successful_executions = len(
            [execution for execution in executions if execution.status == "EXECUTED"]
        )

        failed_executions = total_executions - successful_executions

        if total_executions > 0:

            success_rate = (successful_executions / total_executions) * 100

        else:

            success_rate = 0

        return {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "failed_executions": failed_executions,
            "success_rate": round(
                success_rate,
                2,
            ),
        }
