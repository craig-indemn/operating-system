import { useEffect, useRef } from 'react';

interface ShortcutActions {
  focusPane: (index: number) => void;
  createSession: () => void;
  closePane: () => void;
  escapeMaximize: () => void;
  togglePanel: () => void;
}

export function useKeyboardShortcuts(actions: ShortcutActions): void {
  // Use ref to avoid stale closures — actions object may change every render
  const actionsRef = useRef(actions);
  actionsRef.current = actions;

  useEffect(() => {
    function handler(e: KeyboardEvent) {
      // Don't capture shortcuts when typing in an input/textarea
      const target = e.target as HTMLElement;
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') return;

      const meta = e.metaKey || e.ctrlKey;

      // Cmd+1-9: focus pane by index
      if (meta && e.key >= '1' && e.key <= '9') {
        e.preventDefault();
        actionsRef.current.focusPane(parseInt(e.key) - 1);
        return;
      }

      // Cmd+N: create session
      if (meta && e.key === 'n') {
        e.preventDefault();
        actionsRef.current.createSession();
        return;
      }

      // Cmd+W: close/minimize focused pane
      if (meta && e.key === 'w') {
        e.preventDefault();
        actionsRef.current.closePane();
        return;
      }

      // Escape: restore from maximized
      if (e.key === 'Escape') {
        actionsRef.current.escapeMaximize();
        return;
      }

      // Cmd+B: toggle panel
      if (meta && e.key === 'b') {
        e.preventDefault();
        actionsRef.current.togglePanel();
        return;
      }
    }

    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []); // Empty deps — actionsRef keeps it fresh
}
