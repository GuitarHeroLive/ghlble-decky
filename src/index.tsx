import {
  PanelSection,
  PanelSectionRow,
  ToggleField,
  staticClasses
} from "@decky/ui";

import {
  callable,
  definePlugin
} from "@decky/api"

import { useState, useEffect } from "react";
import { FaGuitar } from "react-icons/fa";

const daemonGetScan = callable<[], boolean>("daemonGetScan");
const daemonSetScan = callable<[enabled: boolean], void>("daemonSetScan");

function Content() {
  const [loading, setLoading] = useState<boolean>(true);
  const [scan, setScan] = useState<boolean>(false);

  useEffect(() => {
    const fetchInitialState = async () => {
      try {
        const initialState = await daemonGetScan();
        setScan(initialState);
      } catch (error) {
        console.error("Failed to fetch initial scan state:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchInitialState();
  }, []);

  const onScanToggle = async (checked: boolean) => {
    setScan(checked);
    daemonSetScan(checked);
  };

  if (loading) {
    return <PanelSection title="Service Control">Loading...</PanelSection>;
  }

  return (
    <PanelSection title="Service Control">
      <PanelSectionRow>
        <ToggleField
          label="Pair Guitars"
          description="Enable, turn on your guitars, then disable once they are connected."
          checked={scan}
          onChange={onScanToggle}
        />
      </PanelSectionRow>
    </PanelSection>
  );
};

export default definePlugin(() => {
  console.log("Guitar Hero Live Plugin is loading...")

  return {
    name: "Guitar Hero Live",
    titleView: <div className={staticClasses.Title}>Guitar Hero Live</div>,
    content: <Content />,
    icon: <FaGuitar />,
    onDismount() {
      console.log("Guitar Hero Live Plugin is unloading...")
    },
  };
});
