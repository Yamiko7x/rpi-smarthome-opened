<template>
  <div class="quickListPanelWrapper">
      <div class="quickListPanel">
        <slot></slot>
      </div>
  </div>
</template>

<script>
export default {
  name: "QuickListPanel",
  props: {
  },
  data() {
    return {
    };
  },
  methods: {
  },
};
</script>

<style lang="scss" scoped>
$quickListPanel-size: 40px;

.quickListPanelWrapper {
  position: fixed;
  top: 0;
  right: 0;
  width: 40%;
  height: 100%;
  z-index: 90;
  background-color: #fff;
  box-shadow: -1px 1px 8px rgba(0,0,0,0.3);
  overflow: auto;

  .quickListPanel {
    padding: 30px;
  }
}
@media only screen and (max-width: 600px) {
  .quickListPanelWrapper {
    width: 100%;
  }
}
</style>