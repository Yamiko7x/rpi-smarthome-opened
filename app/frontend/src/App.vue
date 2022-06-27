<template>
  <div>
    <div v-if="this.$store.state.user">
      <h1><FA-Icon v-if="this.$route.name!='home'" icon="angles-left" class="backIcon" @click='this.$router.push(this.$store.state.goto)'/> {{ this.$store.state.currentView }}</h1>
      <h4>
        <FA-Icon icon="circle-user" style="font-size: 0.85em;"/>
        {{ this.$store.state.user.uname }}
      </h4>
      <br>
    </div>
    <MessageBox />

    <!-- TODO: Quick buttons in one layout -->
    <!-- TODO: Quick buttons can be on another site (some like left hand mode for mobile) -->
    <BackHomeButton v-if="this.$store.state.user" />
    <QuickTipsBtn v-if="this.$store.state.user"/>
    <QuickSwitchPilotAction v-if="this.$store.state.user && this.$store.state.user.edit_actions==1"/>
    <ImgBackground
      :src="this.$store.state.background"
      :blur="this.$store.state.backgroundBlur"
    />
    <router-view />
    <!-- <div class="mobileSpaceBottom"></div> -->
  </div>
</template>

<script>
export default {
  name: "AppTemplate",
  components: {
    BackHomeButton: require("@/components/global_components/BackHomeButton.vue").default,
    ImgBackground: require("@/components/global_components/ImgBackground.vue").default,
    MessageBox: require("@/components/global_components/MessageBox.vue").default,
    QuickTipsBtn: require("@/components/global_components/QuickTipsBtn.vue").default,
    QuickSwitchPilotAction: require("@/components/global_components/QuickSwitchPilotAction.vue").default,
  },
  created() {
    if (this.$store.state.user === null && localStorage.getItem("user")) {
      this.$store.commit(
        "updateUser",
        JSON.parse(localStorage.getItem("user"))
      );
      this.$store.dispatch("isLoggedIn");
      this.$store.commit(
        "restoreBackground",
        localStorage.getItem("backgroundPath")
      );
    }
    console.log(this.$store.state.user)

    if (!localStorage.getItem("backgroundPath"))
      localStorage.setItem("backgroundPath", this.$store.state.background);

    if (!localStorage.getItem("backgroundBlur"))
      localStorage.setItem("backgroundBlur", this.$store.state.backgroundBlur);

    if (localStorage.getItem("refreshWidgetDelay"))
      this.$store.state.refreshWidgetDelay = localStorage.getItem("refreshWidgetDelay");
    else
      localStorage.setItem("refreshWidgetDelay", this.$store.state.refreshWidgetDelay);
  },
};
</script>


<style lang="scss">
/* TODO: uniform global style */

$color-blue: rgb(27, 77, 110);
$color-light-blue: rgb(84, 149, 192);
$transcolor-dark-blue: rgb(27, 77, 110, 0.5);

$color-pastel-blue: rgb(94, 190, 253);
$color-pastel-red: rgb(253, 99, 94);
$color-pastel-dark-red: rgb(189, 62, 58);
$color-pastel-green: rgb(143, 226, 143);
$color-pastel-dark-green: rgb(102, 173, 102);

$color-gray: rgb(161, 161, 161);

$leftBorderSize: 4px;


#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

#app *{
  font-size: 18px;
  }

.mobileSpaceBottom{
  height: 200px;
}

hr{
  border-top: 0.15em dotted #999;
}

.bg-blue{
  background-color: $color-light-blue;
}
.bg-red{
  background-color: $color-pastel-red;
}
.bg-gray, .bgGray{
  background-color: $color-gray;
}
.bgWhite{
  background-color: #fff;
}
.fWhite{
  color: #fff;
}
.borderLeftRed{
  border-left: $leftBorderSize solid $color-pastel-red;
}
.borderLeftGreen{
  border-left: $leftBorderSize solid $color-pastel-green;
}
.borderLeftBlue{
  border-left: $leftBorderSize solid $color-pastel-blue;
}

.backIcon{
  font-size: 0.82em; 
  margin-right: 5px;
  transition: 0.1s;
}
.backIcon:hover{
  color: $color-pastel-red;
  cursor: pointer;
}

/* Quick Menu Button */
$quickBtnBorderColor: rgb(94, 190, 253);
$quickAccessBtnSize: 40px;
.btn-quickAccess {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 10px;
    border-radius: 100%;
    border-right: 1px solid $quickBtnBorderColor;
    border-bottom: 1px solid $quickBtnBorderColor;
    border-top: 1px solid $quickBtnBorderColor;
    background-color: rgb(84, 149, 192);
    color: #fff;
    transition: 0.2s;
    width: $quickAccessBtnSize;
    height: $quickAccessBtnSize;
    
  .faicon{
    /* font-size: 1.4em; */
  }
}
.btn-quickAccess:hover {
  cursor: pointer;
  background-color: rgb(27, 77, 110);
}


/* Widget state style */
.idle, .deactive, .active, .disable{
  background-color: rgb(255, 255, 255);
  border: 3px solid rgba(0, 0, 0, 0);
  transition: all .1s;
}
.deactive{ transition: all .1s; }
.deactive:hover{
  border: 3px solid rgba(0, 0, 0, 0.5);
  cursor: pointer;
}
.active{
  background-color: $color-pastel-green;
}
.active:hover{
  background-color: rgb(101, 209, 101);
  cursor: pointer;
}
.disable{
  background-color: #d3d3d3;
  color: #a5a5a5;
}

.fdeactive{ 
  color: $color-pastel-red;
}
.fdeactive:hover{
  cursor: pointer;
}
.factive{
  color: $color-pastel-green;
}
.factive:hover{
  cursor: pointer;
}

/* Widget menu */
.trash, .edit{
  color: #747474;
  /* font-size: 1.3em; */
  transition: 0.2s;
  margin-left: 10px;
}
.trash:hover{
  color: #b83827;
  cursor: pointer;
}
.edit:hover{
  color: #185977;
  cursor: pointer;
}
.cancel{
  background-color: $color-pastel-red;
}
.cancel:hover, .cancel:focus{
  background-color: $color-pastel-dark-red;
}
.add{
  background-color: $color-pastel-green;
}
.add:hover, .add:focus{
  background-color: $color-pastel-dark-green;
}
.add-dark{
  background-color: $color-pastel-dark-green;
}
.add-dark:hover, .add-dark:focus{
  background-color: $color-pastel-green;
}
.gray-blue{
  background-color: $color-gray;
}
.gray-blue:hover, .gray-blue:focus{
  background-color: $color-light-blue;
}


/* View smooth change */
.hideView {
  transition: all 0.2s;
  opacity: 0;
}
.showView {
  transition: all 0.2s;
  opacity: 1;
}

h1{
  margin-block-start: 0;
  margin-block-end: 0;
  margin-top: 25px;
}

h4{
  margin-block-start: 0;
  margin-block-end: 0;
  font-weight: 200;
}

/* Forms and buttons */
form {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;

  label {
    /* font-size: 1.3em; */
    font-weight: bold;
    color: #fff;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 1);
  }

  div {
    display: flex;
    flex-direction: column;
    padding: 5px;
    width: 80%;
    max-width: 350px;
    min-width: 200px;
  }
}

input,
select {
  border: none;
  transition: 0.2s;
  padding: 5px 15px;
  margin-top: 5px;
  font-size: 1.1em;
  background-color: #fff;
}

input:focus,
select:focus {
  outline: none;
}

input[type="submit"],
button {
  cursor: pointer;
  border: none;
  background-color: $color-light-blue;
  color: #fff;
  padding: 12px 20px;
}
button{
  transition: 0.2s;
}

input[type="submit"]:hover,
input[type="submit"]:focus,
button:hover,
button:focus {
  background-color: $color-blue;
}

.btn-danger {
  background-color: $color-pastel-dark-red;
}
.btn-danger:hover,
.btn-danger:focus {
  background-color: $color-pastel-red;
}

.btn-action {
  background-color: $color-blue;
}
.btn-action:hover,
.btn-action:focus {
  background-color: $color-light-blue;
}

.btn-yellow {
  background-color: rgb(189, 143, 19);
}
.btn-yellow:hover,
.btn-yellow:focus {
  background-color: rgb(236, 193, 72);
}
</style>
