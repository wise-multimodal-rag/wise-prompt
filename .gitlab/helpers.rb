require_relative File.expand_path('triage/assignee.rb', __dir__)

Gitlab::Triage::Resource::Context.include(Assignee)