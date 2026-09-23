import { afterEach, describe, expect, it, vi } from "vitest";
import { createContracts } from "@wanxiang/runtime/modules/contracts";
import {
  interfaceOptions,
  sessionContracts,
} from "../../../src/studio/library/utils";

afterEach(() => vi.unstubAllGlobals());

describe("session connection contracts", () => {
  it("keeps independent registries and reflects definition replacements", () => {
    vi.stubGlobal("WXContracts", { createContracts });
    const first = {
      assets: [],
      interfaces: { "custom.first": { version: 1 } },
    };
    const second = {
      assets: [],
      interfaces: { "custom.second": { version: 2 } },
    };
    const firstContracts = sessionContracts(first)!;
    expect(interfaceOptions(first)).toEqual(["custom.first"]);
    expect(interfaceOptions(second)).toEqual(["custom.second"]);
    first.interfaces = { "custom.first": { version: 3 } };
    expect(sessionContracts(first)!.registry()["custom.first"].version).toBe(3);
    expect(firstContracts.registry()["custom.first"].version).toBe(1);
  });
  it("does not offer contract options in a static review without the kernel", () => {
    vi.stubGlobal("WXContracts", undefined);
    expect(interfaceOptions({ assets: [] })).toEqual([]);
  });
});
