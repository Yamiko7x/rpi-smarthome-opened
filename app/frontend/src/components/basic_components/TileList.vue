<template>
  <ul :class="['dashboardTile', oddTiles() ? 'lastbig' : '']">
    <li v-for="tile in tiles" :key="tile.id" v-on:click="tile.method">
      {{ tile.name }}
    </li>
  </ul>
</template>

<script>
export default {
  name: "TileList",
  props: {tiles : {required : true}},
  data(){
    return { lastbig: {} }
  },
  methods: {
    oddTiles(){
      return this.tiles.length % 2 != 0 ? true : false;
    }
  },
};
</script>

<style lang="scss" scoped>
$tile-margin: 8px;

.dashboardTile {
  list-style-type: none;
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  width: 50%;
  margin: auto;
  padding: 0;
  overflow: auto;

  li {
    list-style-type: none;
    display: flex;
    justify-content: center;
    align-items: center;
    width: 40%;
    height: 100px;
    margin: $tile-margin;
    padding: 0;
    border-radius: 3px;
    background-color: rgb(255, 255, 255);
    box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.1);
    transition: .2s;
    font-size: 1.1em;
  }
  li:hover{
    box-shadow: 1px 1px 8px rgb(27, 77, 110, .5);
    cursor: pointer;
  }
}

.lastbig li:last-child{
  width: calc(80% + calc($tile-margin * 2));
}
@media only screen and (max-width: 700px) {
  .dashboardTile {
    width: 100%;
    li{
      width: calc(35% + calc($tile-margin * 2));
    }
  }
}
@media only screen and (max-width: 500px) {
  .dashboardTile {
    width: 100%;
    li{
      width: calc(80% + calc($tile-margin * 2));
    }
  }
}
</style>