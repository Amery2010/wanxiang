import { fireEvent, render, screen } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import { TasksPanel } from "../../../src/studio/library/TasksPanel";
import type { BuildTasks } from "../../../src/runtime/types";

it("uses a nonmodal drawer with live concurrency, retry and batch progress", () => {
  let limit = 2;
  const retry = vi.fn(),
    close = vi.fn();
  const tasks: BuildTasks = {
    snapshot: () => ({
      limit,
      active: [],
      queued: [],
      history: [
        { id: 1, asset: "chair", phase: "failed", error: "build failed" },
      ],
    }),
    setConcurrency: vi.fn((next) => {
      limit = next;
    }),
    submit: vi.fn(),
    cancel: vi.fn(),
    cancelAll: vi.fn(),
  };
  render(
    <TasksPanel
      tasks={tasks}
      open
      onClose={close}
      onRetryFailed={retry}
      progress={{
        total: 9,
        completed: 4,
        failed: 1,
        skipped: 2,
        running: true,
        cancelled: false,
      }}
    />,
  );
  expect(screen.getByRole("dialog", { name: "构建任务" })).toHaveAttribute(
    "aria-modal",
    "false",
  );
  fireEvent.change(screen.getByLabelText("构建并发数"), {
    target: { value: "3" },
  });
  expect(tasks.setConcurrency).toHaveBeenCalledWith(3);
  fireEvent.click(screen.getByRole("button", { name: /重试失败/ }));
  expect(retry).toHaveBeenCalledOnce();
  expect(screen.getByRole("status")).toHaveTextContent("4 / 9");
  expect(screen.getByText("build failed")).toBeInTheDocument();
  fireEvent.keyDown(screen.getByRole("dialog"), { key: "Escape" });
  expect(close).toHaveBeenCalledOnce();
});
