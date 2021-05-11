<template>
  <section class="section">
    <div class="container">
      <div class="columns">
        <div class="column is-4 is-offset-4">
          <h2 class="title has-text-centered">
            Welcome back!
          </h2>
          <Notification v-if="error" :message="error" />
          <form method="post" @submit.prevent="login">
            <div class="field">
              <label class="label">Email</label>
              <div class="control">
                <input
                  v-model="email"
                  type="email"
                  class="input"
                  name="email"
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
                >
              </div>
            </div>
            <div class="control">
              <button type="submit" class="button is-dark is-fullwidth">
                Log In
              </button>
            </div>
          </form>
          <div class="has-text-centered" style="margin-top: 20px">
            <p>
              Don't have an account?
              <nuxt-link to="/register">
                Register
              </nuxt-link>
            </p>
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
    async login () {
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
