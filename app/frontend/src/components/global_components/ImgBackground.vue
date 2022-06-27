<template>
  <div class="blur-bg" :style="background_img()"></div>
</template>

<script>
export default {
  name: "ImgBackground",
  props: ["src", "blur", "posx"],
  methods: {
    background_img() {
      return {
        "background-image": `url(${this.src})`,
        "filter": `blur(${this.blur}px)`,
        "-webkit-filter": `blur(${this.blur}px)`,
        "background-position": this.posx,
        "transition": `all ${this.$store.state.animationSpeed}ms`,
      };
    },
  },
};
</script>

<style lang="scss" scoped>
.blur-bg {
  position: fixed;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  z-index: -1;
  background-repeat: no-repeat;
  background-size: cover;
  background-position: 20%;
}
</style>