import { expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { CachePanel } from "../../../src/studio/library/CachePanel";
import type { BuildCache } from "../../../src/runtime/types";

it("requires a second action before clearing all build cache", async () => {
  const clean = vi.fn(async () => 1);
  const cache = {
    stats: vi.fn(async () => ({ memory_entries: 1, disk_entries: 2 })),
    clean,
  } as unknown as BuildCache;
  const user = userEvent.setup();
  render(<CachePanel cache={cache} open onClose={vi.fn()} />);
  await user.click(screen.getByRole("button", { name: "清除全部缓存" }));
  expect(clean).not.toHaveBeenCalled();
  expect(
    screen.getByRole("alertdialog", { name: "确认清除全部缓存" }),
  ).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "取消" }));
  expect(clean).not.toHaveBeenCalled();
  await user.click(screen.getByRole("button", { name: "清除全部缓存" }));
  await user.click(screen.getByRole("button", { name: "确认清除" }));
  await waitFor(() => expect(clean).toHaveBeenCalledTimes(1));
  expect(clean).toHaveBeenCalledWith({});
  expect(await screen.findByRole("status")).toHaveTextContent(
    "全部构建缓存已清除",
  );
});
