<template>
  <section class="section">
    <div class="container">
      <div class="columns">
        <div class="column is-4 is-offset-4">
          <h2 class="title has-text-centered">
            Register!
          </h2>
          <Notification v-if="error" :message="error" />
          <form method="post" @submit.prevent="register">
            <div class="field">
              <label class="label">User Name</label>
              <div class="control">
                <input
                  v-model="name"
                  type="text"
                  class="input"
                  name="name"
                  required
                >
              </div>
            </div>
            <div class="field">
              <label class="label">Email</label>
              <div class="control">
                <input
                  v-model="email"
                  type="email"
                  class="input"
                  name="email"
                  required
                >
              </div>
            </div>
            <div class="field">
              <label class="label">Password</label>
              <div class="control">
                <input
                  v-model="password"
                  type="password"
                  class="input"
                  name="password"
                  required
                >
              </div>
            </div>
            <div class="control">
              <button type="submit" class="button is-dark is-fullwidth">
                Register
              </button>
            </div>
          </form>
          <div class="has-text-centered" style="margin-top: 20px">
            Already got an account?
            <nuxt-link to="/login">
              Login
            </nuxt-link>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import Notification from '~/components/Notification'

export default {
  middleware: 'preventInvalidAuthentication',

  components: {
    Notification
  },

  data () {
    return {
      name: '',
      email: '',
      password: '',
      error: null
    }
  },

  methods: {
    async register () {
      const { data: { error: registerError } = {} } = await this.$axios.post('users/register', {
        email: this.email,
        name: this.name,
        password: this.password
      })
      if (registerError) {
        this.error = registerError
        return
      }
      const {
        data: { _id, name, email, error: loginError } = {}
      } = await this.$axios.post('users/login', {
        email: this.email,
        password: this.password
      })
      if (loginError) {
        this.error = loginError
        return
      }
      this.$auth.setUser({
        email,
        name,
        _id
      })
      this.$router.push('/')
    }
  }
}
</script>
