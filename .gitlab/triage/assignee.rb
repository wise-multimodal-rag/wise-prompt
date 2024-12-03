module Assignee
  def assignee
    resource[:assignees]
  end

  def has_assignee?
    assignee && assignee.any?
  end
end
