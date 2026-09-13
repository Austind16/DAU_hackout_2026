(() => {
  const config = window.SUPABASE_CONFIG || {};
  const client = window.supabase?.createClient(config.url || '', config.anonKey || '');

  function getClient() {
    if (!client || !config.url || !config.anonKey) {
      throw new Error('Supabase is not configured. Set url and anonKey in supabase-config.js.');
    }
    return client;
  }

  function getAuthError(error) {
    return error?.message || 'Supabase authentication failed.';
  }

  window.solarShareData = {
    async getSession() {
      const { data, error } = await getClient().auth.getSession();
      if (error) throw new Error(getAuthError(error));
      return data.session;
    },

    async signIn(email, password) {
      const { data, error } = await getClient().auth.signInWithPassword({ email, password });
      if (error) throw new Error(getAuthError(error));
      return data.session;
    },

    async signUp({ email, password, fullName, role }) {
      const { data, error } = await getClient().auth.signUp({
        email,
        password,
        options: {
          data: {
            full_name: fullName,
            operating_role: role
          }
        }
      });
      if (error) throw new Error(getAuthError(error));
      return data;
    },

    async signOut() {
      const { error } = await getClient().auth.signOut();
      if (error) throw new Error(getAuthError(error));
    },

    async getMapHouses() {
      const supabaseClient = getClient();
      const [housesResult, listingsResult, session] = await Promise.all([
        supabaseClient.from('houses').select('*'),
        supabaseClient.from('listings').select('id, house_id, available_kwh, asking_price, status').in('status', ['open', 'active']),
        this.getSession().catch(() => null)
      ]);
      if (housesResult.error) throw new Error(housesResult.error.message);
      if (listingsResult.error) throw new Error(listingsResult.error.message);

      const listingByHouseId = new Map();
      (listingsResult.data || []).forEach(listing => listingByHouseId.set(listing.house_id, listing));
      const currentUserId = session?.user?.id || null;
      return (housesResult.data || []).map(house => ({
        ...house,
        listing: listingByHouseId.get(house.house_id) || null,
        is_me: Boolean(currentUserId) && house.user_id === currentUserId
      }));
    },

    async getBuyerData() {
      const supabaseClient = getClient();
      const [housesResult, listingsResult] = await Promise.all([
        supabaseClient.from('houses').select('*'),
        supabaseClient.from('listings').select('id, house_id, date, available_kwh, asking_price, status').order('date', { ascending: false })
      ]);

      if (housesResult.error) throw new Error(housesResult.error.message);
      if (listingsResult.error) throw new Error(listingsResult.error.message);

      return {
        houses: housesResult.data || [],
        listings: listingsResult.data || []
      };
    },

    async getSellerData({ fallbackHouseId } = {}) {
      const supabaseClient = getClient();
      const session = await this.getSession();
      if (!session?.user?.id) throw new Error('Sign in before opening the Seller dashboard.');

      let { data: house, error: houseError } = await supabaseClient
        .from('houses')
        .select('*')
        .eq('user_id', session.user.id)
        .maybeSingle();
      if (houseError) throw new Error(houseError.message);
      if (!house && fallbackHouseId) {
        const fallbackResult = await supabaseClient
          .from('houses')
          .select('*')
          .eq('house_id', fallbackHouseId)
          .maybeSingle();
        if (fallbackResult.error) throw new Error(fallbackResult.error.message);
        house = fallbackResult.data;
      }
      if (!house) throw new Error('No house is linked to the signed-in user. Select a Seller node or link houses.user_id.');

      const [readingsResult, listingsResult, tradesResult] = await Promise.all([
        supabaseClient.from('daily_readings').select('*').eq('house_id', house.house_id).order('date', { ascending: true }),
        supabaseClient.from('listings').select('*').eq('house_id', house.house_id).order('date', { ascending: false }),
        supabaseClient.from('trades').select('*').eq('seller_house_id', house.house_id).order('timestamp', { ascending: false })
      ]);
      if (readingsResult.error) throw new Error(readingsResult.error.message);
      if (listingsResult.error) throw new Error(listingsResult.error.message);
      if (tradesResult.error) throw new Error(tradesResult.error.message);

      return {
        house,
        readings: readingsResult.data || [],
        listings: listingsResult.data || [],
        trades: tradesResult.data || []
      };
    },

    async createSellerListing({ houseId, availableKwh, askingPrice }) {
      const { data, error } = await getClient()
        .from('listings')
        .insert({
          house_id: houseId,
          date: new Date().toISOString().slice(0, 10),
          available_kwh: availableKwh,
          asking_price: askingPrice,
          status: 'active'
        })
        .select('*')
        .single();
      if (error) throw new Error(error.message);
      return data;
    },

    async getTradeDeskData() {
      const supabaseClient = getClient();
      const [tradesResult, housesResult] = await Promise.all([
        supabaseClient.from('trades').select('*').order('timestamp', { ascending: false }),
        supabaseClient.from('houses').select('house_id, block, flat_no, owner_name')
      ]);
      if (tradesResult.error) throw new Error(tradesResult.error.message);
      if (housesResult.error) throw new Error(housesResult.error.message);
      return { trades: tradesResult.data || [], houses: housesResult.data || [] };
    },

    async createTrade({ buyerHouseId, sellerHouseId, kwh, pricePerKwh, totalPrice, status = 'completed' }) {
      const { data, error } = await getClient().from('trades').insert({
        buyer_house_id: buyerHouseId,
        seller_house_id: sellerHouseId,
        kwh,
        price_per_kwh: pricePerKwh,
        total_price: totalPrice,
        status
      }).select('*').single();
      if (error) throw new Error(error.message);
      return data;
    },

    async createInquiry({ name, category, message }) {
      const { data, error } = await getClient().from('inquiries').insert({
        name,
        category,
        message,
        status: 'submitted'
      }).select('*').single();
      if (error) throw new Error(error.message);
      return data;
    },

    async getInquiries() {
      const { data, error } = await getClient().from('inquiries').select('*').order('created_at', { ascending: false });
      if (error) throw new Error(error.message);
      return data || [];
    }
  };
})();
