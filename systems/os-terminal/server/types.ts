export interface SessionEvent {
  type: string;
  at: string;
  summary?: string;
}

export interface SessionState {
  version: number;
  session_id: string;
  name: string;
  type?: 'shell' | 'claude';
  project: string | null;
  worktree_path: string;
  tmux_session: string;
  status: string;
  additional_dirs: string[];
  permissions: { mode: string };
  model: string;
  created_at: string;
  last_activity: string;
  context_remaining_pct: number;
  git_branch: string;
  events: SessionEvent[];
}
